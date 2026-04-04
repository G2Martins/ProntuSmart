import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestaoCids } from './gestao-cids';

describe('GestaoCids', () => {
    let component: GestaoCids;
    let fixture: ComponentFixture<GestaoCids>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [GestaoCids],
        }).compileComponents();

        fixture = TestBed.createComponent(GestaoCids);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
